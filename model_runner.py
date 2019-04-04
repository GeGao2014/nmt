from data_loader import DataLoader
from base_seq2seq import Base, Attention, Encoder, Decoder
from torch import nn, optim

def main():
    english_data, german_data = get_data()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = create_model(english_data, german_data, device)
    params = {}
    params['batch_size'] = 16
    params['epochs'] = 1
    params['learning_rate'] = 0.001

    train(english_data['train'][:256], english_data['dev'][:256],
          german_data['train'][:256], german_data['dev'][:256], model, params)

def create_model(english_data, german_data, device):    
    INPUT_DIM = len(german_data['idx2word'])
    OUTPUT_DIM = len(english_data['idx2word'])
    ENC_EMB_DIM = 256
    DEC_EMB_DIM = 256
    ENC_HID_DIM = 512
    DEC_HID_DIM = 512
    ENC_DROPOUT = 0.5
    DEC_DROPOUT = 0.5
    attn = Attention(ENC_HID_DIM, DEC_HID_DIM)
    enc = Encoder(INPUT_DIM, ENC_EMB_DIM, ENC_HID_DIM,
                  DEC_HID_DIM, ENC_DROPOUT)
    dec = Decoder(OUTPUT_DIM, DEC_EMB_DIM, ENC_HID_DIM,
                  DEC_HID_DIM, DEC_DROPOUT, attn)
    model = Base(enc, dec, device).to(device)


def get_data():
    file_loader = DataLoader()
    german_data = file_loader.get_german()
    english_data = file_loader.get_english()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    english_data['train'] = torch.LongTensor(english_data['train']).cuda()
    english_data['dev'] = torch.LongTensor(english_data['dev']).cuda()
    german_data['train'] = torch.LongTensor(german_data['train']).cuda()
    german_data['dev'] = torch.LongTensor(german_data['dev']).cuda()
    return english_data, german_data

def train(eng_train, eng_dev, de_train, de_dev, net, params):
  
    # padding is 0
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    
    optimizer = optim.Adam(net.parameters(), lr=params['learning_rate'])
    
    num_examples, eng_len = eng_train.size()    
    batches = [(start, start + params['batch_size']) for start in\
               range(0, num_examples, params['batch_size'])]
    
    
    for epoch in range(params['epochs']):
        ep_loss = 0.
        start_time = time.time()
        random.shuffle(batches)
        
        # for each batch, calculate loss and optimize model parameters            
        for b_idx, (start, end) in enumerate(batches):
            
            de_src = de_train[start:end]
            eng_trg = eng_train[start:end]
            print("de_src size: ", de_src.size())
            preds = net(de_src, eng_trg)
            
            # q1.1: explain the below line!
            preds = preds[1:].view(-1, preds.shape[-1])
            print("preds size ", preds.size())
            eng_trg = eng_trg[1:].view(-1)
            print("trg size ", eng_trg.size())
            loss = criterion(preds, eng_trg)
            
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
            ep_loss += loss

        print('epoch: {0}, loss: {1}, time: {2}'.format(epoch, ep_loss, time.time()-start_time))


if __name__ == "__main__":
    main()
